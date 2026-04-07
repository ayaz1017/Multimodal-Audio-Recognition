from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import json
import numpy as np
from pathlib import Path
import uuid

from utils.audio_processor import AudioProcessor
from utils.video_processor import VideoProcessor
from utils.report_generator import ReportGenerator
from routes.auth import token_required
from models.database import Patient, AnalysisResult, Report, ensure_db

def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def create_api_blueprint():
    """Create API blueprint with all routes"""
    api = Blueprint('api', __name__)
    
    @api.route('/recognize_audio', methods=['POST'])
    def recognize_audio():
        """
        Recognize emotions/content from audio file
        Expects: audio file (multipart/form-data)
        Optional: patient_id (form-data), requires authentication
        """
        filepath = None
        try:
            # Check if model is loaded
            if not current_app.model:
                return jsonify({'error': 'Model not loaded'}), 500
            
            # Check if file is in request
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if not allowed_file(file.filename, {'wav', 'mp3', 'm4a', 'ogg', 'flac'}):
                return jsonify({'error': 'Invalid audio format'}), 400
            
            # Save file temporarily
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            
            # Process audio
            processor = AudioProcessor()
            features = processor.extract_all_features(filepath)
            
            # Get model predictions
            audio_tensor = processor.process_for_model(
                filepath,
                expected_feature_count=getattr(current_app.model, 'expected_feature_count', None),
                scaler=getattr(current_app.model, 'scaler', None),
                n_mels=getattr(current_app.model, 'n_mels', None),
            )
            predictions = current_app.model.predict(audio_tensor)
            
            # Extract prediction values safely
            pred_values = predictions['predictions']
            prob_values = predictions['probabilities']
            
            # Handle both list and numpy array formats
            if isinstance(pred_values, list):
                pred_idx = pred_values[0]
            else:
                pred_idx = int(pred_values[0])
            
            # Extract confidence - get max probability for this prediction
            if isinstance(prob_values, list):
                probs_first = prob_values[0] if prob_values else []
                prob_val = max(probs_first) if probs_first else 0.0
            else:
                prob_val = float(np.max(prob_values[0]))
            
            # Ensure probability is in valid range [0, 1]
            prob_val = min(max(prob_val, 0.0), 1.0)
            
            # Prepare response
            emotion_names = getattr(current_app.model, 'class_names', []) or [
                'angry',
                'disgust',
                'fear',
                'happy',
                'neutral',
                'sad',
            ]

            emoji_map = {
                'angry': '😠',
                'disgust': '😒',
                'fear': '😨',
                'happy': '😊',
                'neutral': '😐',
                'sad': '😢',
                'surprise': '😲',
            }

            emotion_name = (
                emotion_names[pred_idx]
                if 0 <= pred_idx < len(emotion_names)
                else 'unknown'
            )
            
            response_data = {
                'success': True,
                'audio_features': {
                    'mfcc': features['mfcc'].tolist(),
                    'spectral': features['spectral'].tolist(),
                    'temporal': features['temporal'].tolist(),
                    'duration': features['duration'],
                    'sample_rate': features['sample_rate']
                },
                'predictions': {
                    'prediction': pred_idx,
                    'emotion': emotion_name,
                    'emoji': emoji_map.get(str(emotion_name).lower(), '❓'),
                    'probability': prob_val
                }
            }
            
            # Check if patient_id is provided for saving
            patient_id = request.form.get('patient_id')
            if patient_id:
                # Get auth token from header
                token = None
                if request.headers.get('Authorization'):
                    token = request.headers.get('Authorization').split(' ')[-1]
                
                if not token:
                    if filepath and os.path.exists(filepath):
                        os.remove(filepath)
                    return jsonify({'error': 'Authentication required to save analysis'}), 401
                
                try:
                    from routes.auth import verify_token
                    user_data = verify_token(token)
                    
                    # Verify patient belongs to user
                    ensure_db()
                    patient = Patient.get_by_id(patient_id)
                    if not patient or patient['user_id'] != user_data['user_id']:
                        if filepath and os.path.exists(filepath):
                            os.remove(filepath)
                        return jsonify({'error': 'Unauthorized to access this patient'}), 403
                    
                    # Save analysis to database
                    result = AnalysisResult.create(
                        patient_id=patient_id,
                        analysis_type='audio',
                        file_name=filename,
                        audio_features=json.dumps(response_data['audio_features']),
                        predictions=json.dumps(response_data['predictions']),
                        notes=request.form.get('notes', '')
                    )
                    
                    if result:
                        response_data['result_id'] = result.get('result_id')
                        response_data['saved'] = True
                        response_data['message'] = 'Analysis saved to patient record'
                        
                        # Generate and save comprehensive report
                        try:
                            report_data = ReportGenerator.generate_audio_report(
                                patient_data=patient,
                                analysis_results=response_data
                            )
                            
                            report = Report.create(
                                patient_id=patient_id,
                                result_id=result['result_id'],
                                analysis_type='Audio',
                                report_title=report_data['title'],
                                report_summary=json.dumps(report_data),
                                emotion_detected=response_data['predictions']['emotion'],
                                confidence_score=response_data['predictions']['probability'],
                                audio_features_json=json.dumps(response_data['audio_features']),
                                recommendations=json.dumps(report_data.get('recommendations', []))
                            )
                            
                            if report:
                                response_data['report_id'] = report.get('report_id')
                                response_data['report_generated'] = True
                        except Exception as report_err:
                            response_data['report_generated'] = False
                            response_data['report_warning'] = f'Report generation failed: {str(report_err)}'
                    
                except Exception as e:
                    response_data['saved'] = False
                    response_data['warning'] = f'Analysis completed but not saved: {str(e)}'
            
            # Clean up
            if filepath and os.path.exists(filepath):
                os.remove(filepath)
            
            return jsonify(response_data), 200
        
        except Exception as e:
            if filepath and os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except OSError:
                    pass
            return jsonify({'error': str(e)}), 500
    
    @api.route('/recognize_video', methods=['POST'])
    def recognize_video():
        """
        Recognize facial expressions from video file
        Expects: video file (multipart/form-data)
        Optional: patient_id (form-data), requires authentication
        """
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if not allowed_file(file.filename, {'mp4', 'avi', 'mov', 'mkv'}):
                return jsonify({'error': 'Invalid video format'}), 400
            
            # Save file temporarily
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process video
            processor = VideoProcessor()
            video_info = processor.get_video_info(filepath)
            facial_expressions = processor.extract_facial_expressions(filepath)
            
            # Prepare response
            response_data = {
                'success': True,
                'video_info': video_info,
                'facial_expressions': facial_expressions
            }
            
            # Check if patient_id is provided for saving
            patient_id = request.form.get('patient_id')
            if patient_id:
                # Get auth token from header
                token = None
                if request.headers.get('Authorization'):
                    token = request.headers.get('Authorization').split(' ')[-1]
                
                if not token:
                    os.remove(filepath)
                    return jsonify({'error': 'Authentication required to save analysis'}), 401
                
                try:
                    from routes.auth import verify_token
                    user_data = verify_token(token)
                    
                    # Verify patient belongs to user
                    ensure_db()
                    patient = Patient.get_by_id(patient_id)
                    if not patient or patient['user_id'] != user_data['user_id']:
                        os.remove(filepath)
                        return jsonify({'error': 'Unauthorized to access this patient'}), 403
                    
                    # Save analysis to database
                    result = AnalysisResult.create(
                        patient_id=patient_id,
                        analysis_type='video',
                        file_name=filename,
                        facial_expressions=json.dumps(facial_expressions),
                        predictions=json.dumps(video_info),
                        notes=request.form.get('notes', '')
                    )
                    
                    if result:
                        response_data['result_id'] = result.get('result_id')
                        response_data['saved'] = True
                        response_data['message'] = 'Analysis saved to patient record'
                        
                        # Generate and save comprehensive report
                        try:
                            analysis_result = {
                                'dominant_emotion': facial_expressions.get('dominant_emotion', 'Unknown'),
                                'total_frames_analyzed': video_info.get('total_frames', 0),
                                'emotion_stats': facial_expressions.get('emotion_stats', {}),
                                'emotion_history': facial_expressions.get('emotion_history', [])
                            }
                            
                            report_data = ReportGenerator.generate_video_report(
                                patient_data=patient,
                                analysis_results=analysis_result
                            )
                            
                            report = Report.create(
                                patient_id=patient_id,
                                result_id=result['result_id'],
                                analysis_type='Video',
                                report_title=report_data['title'],
                                report_summary=json.dumps(report_data),
                                emotion_detected=analysis_result['dominant_emotion'],
                                confidence_score=max((stats['mean'] for stats in analysis_result['emotion_stats'].values() if stats['mean'] > 0), default=0.0),
                                video_features_json=json.dumps(analysis_result['emotion_stats']),
                                recommendations=json.dumps(report_data.get('recommendations', []))
                            )
                            
                            if report:
                                response_data['report_id'] = report.get('report_id')
                                response_data['report_generated'] = True
                        except Exception as report_err:
                            response_data['report_generated'] = False
                            response_data['report_warning'] = f'Report generation failed: {str(report_err)}'
                    
                except Exception as e:
                    response_data['saved'] = False
                    response_data['warning'] = f'Analysis completed but not saved: {str(e)}'
            
            # Clean up
            os.remove(filepath)
            
            return jsonify(response_data), 200
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @api.route('/recognize_multimodal', methods=['POST'])
    def recognize_multimodal():
        """
        Recognize using both audio and video (multimodal)
        Expects: video file containing both audio and video
        Optional: patient_id (form-data), requires authentication
        """
        try:
            # Check if model is loaded
            if not current_app.model:
                return jsonify({'error': 'Model not loaded'}), 500
            
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if not allowed_file(file.filename, {'mp4', 'avi', 'mov', 'mkv'}):
                return jsonify({'error': 'Invalid video format'}), 400
            
            # Save file temporarily
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Extract audio from video
            audio_filename = f"audio_{filename}.wav"
            audio_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], audio_filename)
            
            # Process video for facial expressions
            video_processor = VideoProcessor()
            video_info = video_processor.get_video_info(filepath)
            facial_expressions = video_processor.extract_facial_expressions(filepath)
            
            # Extract audio from video
            audio_filepath = video_processor.extract_audio_from_video(filepath, audio_filepath)
            
            # Process audio
            audio_processor = AudioProcessor()
            audio_features = audio_processor.extract_all_features(audio_filepath)
            audio_tensor = audio_processor.process_for_model(
                audio_filepath,
                expected_feature_count=getattr(current_app.model, 'expected_feature_count', None),
                scaler=getattr(current_app.model, 'scaler', None),
                n_mels=getattr(current_app.model, 'n_mels', None),
            )
            audio_predictions = current_app.model.predict(audio_tensor)

            pred_values = audio_predictions.get('predictions', [])
            prob_values = audio_predictions.get('probabilities', [])
            pred_idx = int(pred_values[0]) if pred_values else -1
            probs_first = prob_values[0] if prob_values else []
            prob_val = float(max(probs_first)) if probs_first else 0.0

            emotion_names = getattr(current_app.model, 'class_names', [])
            emotion_name = (
                emotion_names[pred_idx]
                if 0 <= pred_idx < len(emotion_names)
                else 'unknown'
            )
            
            # Combine results
            combined_result = {
                'audio': {
                    'features': {
                        'mfcc': audio_features['mfcc'].tolist(),
                        'spectral': audio_features['spectral'].tolist(),
                        'temporal': audio_features['temporal'].tolist(),
                        'duration': audio_features['duration'],
                        'sample_rate': audio_features['sample_rate']
                    },
                    'predictions': {
                        'prediction': pred_idx,
                        'emotion': emotion_name,
                        'probability': prob_val
                    }
                },
                'video': {
                    'info': video_info,
                    'facial_expressions': facial_expressions
                },
                'combined_analysis': {
                    'dominant_emotion': facial_expressions['dominant_emotion'],
                    'audio_prediction_confidence': prob_val,
                    'recommendation': 'Use combined results for better accuracy'
                }
            }
            
            # Prepare response
            response_data = {
                'success': True,
                'data': combined_result
            }
            
            # Check if patient_id is provided for saving
            patient_id = request.form.get('patient_id')
            if patient_id:
                # Get auth token from header
                token = None
                if request.headers.get('Authorization'):
                    token = request.headers.get('Authorization').split(' ')[-1]
                
                if not token:
                    os.remove(filepath)
                    if os.path.exists(audio_filepath):
                        os.remove(audio_filepath)
                    return jsonify({'error': 'Authentication required to save analysis'}), 401
                
                try:
                    from routes.auth import verify_token
                    user_data = verify_token(token)
                    
                    # Verify patient belongs to user
                    ensure_db()
                    patient = Patient.get_by_id(patient_id)
                    if not patient or patient['user_id'] != user_data['user_id']:
                        os.remove(filepath)
                        if os.path.exists(audio_filepath):
                            os.remove(audio_filepath)
                        return jsonify({'error': 'Unauthorized to access this patient'}), 403
                    
                    # Save analysis to database
                    result = AnalysisResult.create(
                        patient_id=patient_id,
                        analysis_type='multimodal',
                        file_name=filename,
                        audio_features=json.dumps(combined_result['audio']['features']),
                        predictions=json.dumps(combined_result['audio']['predictions']),
                        facial_expressions=json.dumps(combined_result['video']['facial_expressions']),
                        combined_analysis=json.dumps(combined_result['combined_analysis']),
                        notes=request.form.get('notes', '')
                    )
                    
                    if result:
                        response_data['result_id'] = result.get('result_id')
                        response_data['saved'] = True
                        response_data['message'] = 'Analysis saved to patient record'
                        
                        # Generate and save comprehensive multimodal report
                        try:
                            audio_analysis = {
                                'predictions': {
                                    'prediction': combined_result['audio']['predictions']['prediction'],
                                    'probability': combined_result['audio']['predictions']['probability']
                                },
                                'audio_features': combined_result['audio']['features']
                            }
                            
                            video_analysis = {
                                'dominant_emotion': combined_result['video']['facial_expressions'].get('dominant_emotion', 'Unknown'),
                                'total_frames_analyzed': combined_result['video']['info'].get('total_frames', 0),
                                'emotion_stats': combined_result['video']['facial_expressions'].get('emotion_stats', {}),
                                'emotion_history': combined_result['video']['facial_expressions'].get('emotion_history', [])
                            }
                            
                            report_data = ReportGenerator.generate_multimodal_report(
                                patient_data=patient,
                                audio_analysis=audio_analysis,
                                video_analysis=video_analysis
                            )
                            
                            report = Report.create(
                                patient_id=patient_id,
                                result_id=result['result_id'],
                                analysis_type='Multimodal',
                                report_title=report_data['title'],
                                report_summary=json.dumps(report_data),
                                emotion_detected='Multimodal',
                                confidence_score=report_data['combined_analysis']['overall_confidence'] / 100.0,
                                audio_features_json=json.dumps(combined_result['audio']['features']),
                                video_features_json=json.dumps(combined_result['video']['facial_expressions'].get('emotion_stats', {})),
                                recommendations=json.dumps(report_data.get('recommendations', []))
                            )
                            
                            if report:
                                response_data['report_id'] = report.get('report_id')
                                response_data['report_generated'] = True
                        except Exception as report_err:
                            response_data['report_generated'] = False
                            response_data['report_warning'] = f'Report generation failed: {str(report_err)}'
                    
                except Exception as e:
                    response_data['saved'] = False
                    response_data['warning'] = f'Analysis completed but not saved: {str(e)}'
            
            # Clean up
            os.remove(filepath)
            if os.path.exists(audio_filepath):
                os.remove(audio_filepath)
            
            return jsonify(response_data), 200
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @api.route('/reports/<patient_id>', methods=['GET'])
    def get_patient_reports(patient_id):
        """
        Get all reports for a patient
        Requires authentication
        """
        try:
            # Get auth token from header
            token = None
            if request.headers.get('Authorization'):
                token = request.headers.get('Authorization').split(' ')[-1]
            
            if not token:
                return jsonify({'error': 'Authentication required'}), 401
            
            try:
                from routes.auth import verify_token
                user_data = verify_token(token)
                
                # Verify patient belongs to user
                ensure_db()
                patient = Patient.get_by_id(patient_id)
                if not patient or patient['user_id'] != user_data['user_id']:
                    return jsonify({'error': 'Unauthorized to access this patient'}), 403
                
                # Get reports
                reports = Report.get_by_patient(patient_id)
                
                return jsonify({
                    'success': True,
                    'patient_id': patient_id,
                    'patient_name': patient['name'],
                    'reports': reports,
                    'total_reports': len(reports)
                }), 200
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @api.route('/reports/detail/<report_id>', methods=['GET'])
    def get_report_detail(report_id):
        """
        Get detailed report by report ID
        Requires authentication
        """
        try:
            # Get auth token from header
            token = None
            if request.headers.get('Authorization'):
                token = request.headers.get('Authorization').split(' ')[-1]
            
            if not token:
                return jsonify({'error': 'Authentication required'}), 401
            
            try:
                from routes.auth import verify_token
                user_data = verify_token(token)
                
                # Get report
                ensure_db()
                report = Report.get_by_id(report_id)
                
                if not report:
                    return jsonify({'error': 'Report not found'}), 404
                
                # Verify patient belongs to user
                patient = Patient.get_by_id(report['patient_id'])
                if not patient or patient['user_id'] != user_data['user_id']:
                    return jsonify({'error': 'Unauthorized to access this report'}), 403
                
                # Parse report summary JSON
                report_detail = report.copy()
                try:
                    report_detail['report_summary'] = json.loads(report['report_summary'])
                    report_detail['recommendations'] = json.loads(report['recommendations'])
                    if report['audio_features_json']:
                        report_detail['audio_features'] = json.loads(report['audio_features_json'])
                    if report['video_features_json']:
                        report_detail['video_features'] = json.loads(report['video_features_json'])
                except:
                    pass  # Keep as-is if parsing fails
                
                return jsonify({
                    'success': True,
                    'report': report_detail
                }), 200
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @api.route('/test', methods=['GET'])
    def test():
        """Test endpoint"""
        return jsonify({
            'message': 'API is working',
            'model_status': 'loaded' if current_app.model else 'not loaded'
        }), 200
    
    return api
