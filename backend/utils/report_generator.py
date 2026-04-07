"""
Report generation for audio and video emotion analysis
"""
import json
from datetime import datetime

EMOTION_MAP = {
    0: "Angry",
    1: "Disgust", 
    2: "Fear",
    3: "Happy",
    4: "Neutral",
    5: "Sad",
    6: "Surprise"
}

EMOTION_DESCRIPTIONS = {
    "Angry": "The speaker appears to be expressing anger or frustration. Voice qualities typically include elevated pitch, rapid speech, and tense vocal characteristics.",
    "Disgust": "The speaker shows signs of disgust or disapproval. This is often conveyed through vocal quality changes and specific speech patterns.",
    "Fear": "The speaker exhibits characteristics of fear or anxiety. Common features include hesitation, higher pitch, and variable speech rate.",
    "Happy": "The speaker demonstrates positive emotions and happiness. Typically characterized by higher pitch, faster speech rate, and brighter vocal quality.",
    "Neutral": "The speaker maintains a neutral or objective tone. Speech is typically measured with consistent pitch and rate.",
    "Sad": "The speaker expresses sadness or melancholy. Often characterized by lower pitch, slower speech rate, and reduced vocal intensity.",
    "Surprise": "The speaker shows signs of surprise or astonishment. Typically marked by pitch changes, variable speech rate, and sudden vocal shifts."
}

class ReportGenerator:
    """Generate comprehensive emotion analysis reports"""
    
    @staticmethod
    def generate_audio_report(patient_data, analysis_results):
        """Generate an audio analysis report"""
        
        emotion_id = analysis_results['predictions']['prediction']
        emotion_name = EMOTION_MAP.get(emotion_id, "Unknown")
        confidence = analysis_results['predictions']['probability']
        
        # Extract features
        mfcc = analysis_results['audio_features'].get('mfcc', [])
        spectral = analysis_results['audio_features'].get('spectral', [])
        temporal = analysis_results['audio_features'].get('temporal', [])
        duration = analysis_results['audio_features'].get('duration', 0)
        sample_rate = analysis_results['audio_features'].get('sample_rate', 22050)
        
        # Generate report
        report = {
            'title': f"Audio Emotion Analysis Report - {emotion_name}",
            'patient_name': patient_data['name'],
            'analysis_date': datetime.now().isoformat(),
            'analysis_type': 'Audio',
            'duration_seconds': round(duration, 2),
            'sample_rate': sample_rate,
            
            'emotion_analysis': {
                'detected_emotion': emotion_name,
                'confidence': round(confidence * 100, 2),
                'description': EMOTION_DESCRIPTIONS.get(emotion_name, "")
            },
            
            'audio_features': {
                'mfcc': {
                    'values': [round(v, 3) for v in mfcc],
                    'count': len(mfcc),
                    'description': 'Mel-Frequency Cepstral Coefficients - captures vocal tone and pitch characteristics'
                },
                'spectral_features': {
                    'zero_crossing_rate': round(spectral[0], 4) if len(spectral) > 0 else 0,
                    'spectral_centroid_hz': round(spectral[1], 2) if len(spectral) > 1 else 0,
                    'spectral_rolloff_hz': round(spectral[2], 2) if len(spectral) > 2 else 0,
                    'description': 'Frequency domain characteristics of the audio'
                },
                'temporal_features': {
                    'energy': round(temporal[0], 2) if len(temporal) > 0 else 0,
                    'rms_amplitude': round(temporal[1], 4) if len(temporal) > 1 else 0,
                    'description': 'Time domain energy and amplitude characteristics'
                }
            },
            
            'recommendations': ReportGenerator._get_audio_recommendations(emotion_name, confidence),
            
            'technical_details': {
                'model': 'Deep Neural Network (DNN Classifier)',
                'input_features': 18,
                'architecture': 'Simple DNN with 3 layers',
                'output_classes': 7
            }
        }
        
        return report
    
    @staticmethod
    def generate_video_report(patient_data, analysis_results):
        """Generate a video/facial expression analysis report"""
        
        emotional_expressions = analysis_results.get('emotion_history', [])
        emotion_stats = analysis_results.get('emotion_stats', {})
        dominant_emotion = analysis_results.get('dominant_emotion', 'Unknown')
        
        # Calculate statistics
        if emotion_stats:
            confidence = max([stats['mean'] for stats in emotion_stats.values() if stats['mean'] > 0], default=0)
        else:
            confidence = 0
        
        report = {
            'title': f"Video Facial Expression Analysis Report - {dominant_emotion}",
            'patient_name': patient_data['name'],
            'analysis_date': datetime.now().isoformat(),
            'analysis_type': 'Video',
            
            'emotion_analysis': {
                'dominant_emotion': dominant_emotion,
                'confidence': round(confidence * 100, 2),
                'description': EMOTION_DESCRIPTIONS.get(dominant_emotion, "")
            },
            
            'emotion_statistics': {
                'total_frames_analyzed': analysis_results.get('total_frames_analyzed', 0),
                'emotion_breakdown': {
                    emotion: {
                        'occurrences': stats['count'],
                        'average_confidence': round(stats['mean'], 3),
                        'max_confidence': round(stats['max'], 3),
                        'min_confidence': round(stats['min'], 3)
                    }
                    for emotion, stats in emotion_stats.items()
                    if stats['count'] > 0
                }
            },
            
            'emotion_timeline': emotional_expressions[:50],  # Sample of emotion expressions
            
            'recommendations': ReportGenerator._get_video_recommendations(dominant_emotion, confidence),
            
            'technical_details': {
                'method': 'Deep Learning Face Detection and Facial Expression Recognition',
                'detector': 'Haar Cascade + Fallback Face Detection',
                'emotion_classes': 7,
                'note': 'Using fallback detection as advanced model not available'
            }
        }
        
        return report
    
    @staticmethod
    def generate_multimodal_report(patient_data, audio_analysis, video_analysis):
        """Generate a combined multimodal analysis report"""
        
        audio_emotion = EMOTION_MAP.get(audio_analysis['predictions']['prediction'], 'Unknown')
        audio_confidence = audio_analysis['predictions']['probability']
        
        video_emotion = video_analysis.get('dominant_emotion', 'Unknown')
        emotion_stats = video_analysis.get('emotion_stats', {})
        if emotion_stats and video_emotion in emotion_stats:
            video_confidence = emotion_stats[video_emotion]['mean']
        else:
            video_confidence = 0
        
        # Determine overall emotion (weighted average)
        if audio_confidence + video_confidence > 0:
            combined_confidence = (audio_confidence * 0.6 + video_confidence * 0.4)
        else:
            combined_confidence = 0
        
        # Determine if emotions align
        emotions_align = audio_emotion == video_emotion
        
        report = {
            'title': f"Multimodal Emotion Analysis Report",
            'patient_name': patient_data['name'],
            'analysis_date': datetime.now().isoformat(),
            'analysis_type': 'Multimodal (Audio + Video)',
            
            'combined_analysis': {
                'overall_confidence': round(combined_confidence * 100, 2),
                'emotions_align': emotions_align,
                'alignment_note': "Audio and video emotion predictions are consistent" if emotions_align else "Audio and video show different emotions - may indicate conflicting signals"
            },
            
            'audio_component': {
                'detected_emotion': audio_emotion,
                'confidence': round(audio_confidence * 100, 2),
                'description': EMOTION_DESCRIPTIONS.get(audio_emotion, "")
            },
            
            'video_component': {
                'detected_emotion': video_emotion,
                'confidence': round(video_confidence * 100, 2),
                'description': EMOTION_DESCRIPTIONS.get(video_emotion, "")
            },
            
            'recommendations': ReportGenerator._get_multimodal_recommendations(
                audio_emotion, video_emotion, emotions_align, combined_confidence
            ),
            
            'technical_details': {
                'audio_model': 'Deep Neural Network (DNN Classifier)',
                'video_model': 'Facial Expression Recognition with Face Detection',
                'fusion_method': 'Weighted Average (Audio: 60%, Video: 40%)',
                'total_features_analyzed': 18 + video_analysis.get('total_frames_analyzed', 0)
            }
        }
        
        return report
    
    @staticmethod
    def _get_audio_recommendations(emotion, confidence):
        """Get recommendations based on detected emotion"""
        recommendations = []
        
        if emotion == "Angry":
            recommendations = [
                "Consider stress management or conflict resolution techniques",
                "Take breaks during conversations if possible",
                "Practice deep breathing exercises to calm emotions"
            ]
        elif emotion == "Sad":
            recommendations = [
                "Consider supportive counseling or therapy",
                "Engage in activities that improve mood",
                "Reach out to supportive friends or family"
            ]
        elif emotion == "Fear":
            recommendations = [
                "Identify sources of anxiety",
                "Consider anxiety management techniques",
                "Professional support may be beneficial"
            ]
        elif emotion == "Happy":
            recommendations = [
                "Maintain positive behavioral patterns",
                "Continue engaging in fulfilling activities",
                "Share positive emotions with others"
            ]
        elif emotion == "Neutral":
            recommendations = [
                "Monitor ongoing emotional state",
                "Regular check-ins are recommended",
                "No immediate concerns detected"
            ]
        else:
            recommendations = [
                "Continue regular monitoring",
                "Note any patterns in emotional expressions",
                "Follow up with additional analysis if needed"
            ]
        
        if confidence < 0.5:
            recommendations.append("Note: Low confidence - consider additional evaluation")
        
        return recommendations
    
    @staticmethod
    def _get_video_recommendations(emotion, confidence):
        """Get video-specific recommendations"""
        recommendations = []
        
        if emotion == "Angry":
            recommendations = [
                "Monitor facial expressions during interactions",
                "Consider conflict resolution strategies",
                "Track if anger patterns are recurring"
            ]
        elif emotion == "Sad":
            recommendations = [
                "Monitor for persistent sad expressions",
                "Consider follow-up assessments",
                "Supportive intervention may be beneficial"
            ]
        elif emotion == "Fear":
            recommendations = [
                "Investigate triggers for fearful expressions",
                "Consider anxiety assessment",
                "Professional evaluation recommended"
            ]
        elif emotion == "Happy":
            recommendations = [
                "Maintain positive interactions",
                "Continue current positive behavioral patterns",
                "Encourage social engagement"
            ]
        else:
            recommendations = [
                "Continue monitoring facial expressions",
                "Regular assessments recommended",
                "Watch for changes in expression patterns"
            ]
        
        if confidence < 0.6:
            recommendations.append("Note: Ambiguous facial expressions - multiple interpretations possible")
        
        return recommendations
    
    @staticmethod
    def _get_multimodal_recommendations(audio_emotion, video_emotion, align, confidence):
        """Get multimodal-specific recommendations"""
        recommendations = []
        
        if align:
            recommendations.append(f"Audio and video are consistent in detecting {audio_emotion}")
            recommendations.append("High confidence in emotion recognition from multiple modalities")
        else:
            recommendations.append(f"Note: Audio suggests {audio_emotion} while video suggests {video_emotion}")
            recommendations.append("May indicate complex emotional state or mixed signals")
            recommendations.append("Consider individual modality analysis for clarification")
        
        if confidence > 0.8:
            recommendations.append("Strong confidence in overall emotion assessment")
        elif confidence < 0.5:
            recommendations.append("Low confidence - recommend additional evaluation")
        
        recommendations.append("Follow-up analysis recommended to track emotional patterns over time")
        
        return recommendations
