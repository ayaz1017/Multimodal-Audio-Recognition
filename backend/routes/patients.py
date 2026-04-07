from flask import Blueprint, request, jsonify
from routes.auth import token_required
from models.database import Patient, AnalysisResult, ensure_db
import json

patient_bp = Blueprint('patients', __name__)

@patient_bp.route('', methods=['POST'])
@token_required
def create_patient():
    """Create a new patient record"""
    try:
        ensure_db()
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({'error': 'Patient name is required'}), 400
        
        # Create patient
        patient = Patient.create(
            user_id=request.user_id,
            name=data.get('name'),
            age=data.get('age'),
            gender=data.get('gender'),
            phone=data.get('phone'),
            email=data.get('email'),
            medical_history=data.get('medical_history')
        )
        
        if not patient:
            return jsonify({'error': 'Failed to create patient'}), 500
        
        return jsonify({
            'success': True,
            'message': 'Patient created successfully',
            'patient': patient
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@patient_bp.route('', methods=['GET'])
@token_required
def get_patients():
    """Get all patients for current user"""
    try:
        ensure_db()
        patients = Patient.get_by_user(request.user_id)
        
        return jsonify({
            'success': True,
            'patients': patients,
            'count': len(patients)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/<patient_id>', methods=['GET'])
@token_required
def get_patient(patient_id):
    """Get specific patient details"""
    try:
        ensure_db()
        patient = Patient.get_by_id(patient_id)
        
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Verify patient belongs to current user
        if patient['user_id'] != request.user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Get analysis history
        results = AnalysisResult.get_by_patient(patient_id)
        
        return jsonify({
            'success': True,
            'patient': patient,
            'analysis_history': results,
            'total_analyses': len(results)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/<patient_id>', methods=['PUT'])
@token_required
def update_patient(patient_id):
    """Update patient information"""
    try:
        ensure_db()
        patient = Patient.get_by_id(patient_id)
        
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Verify patient belongs to current user
        if patient['user_id'] != request.user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        success = Patient.update(patient_id, **data)
        
        if not success:
            return jsonify({'error': 'Failed to update patient'}), 500
        
        # Get updated patient
        updated_patient = Patient.get_by_id(patient_id)
        
        return jsonify({
            'success': True,
            'message': 'Patient updated successfully',
            'patient': updated_patient
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/<patient_id>/analysis', methods=['POST'])
@token_required
def save_analysis(patient_id):
    """Save analysis result for a patient"""
    try:
        ensure_db()
        patient = Patient.get_by_id(patient_id)
        
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Verify patient belongs to current user
        if patient['user_id'] != request.user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        # Create analysis result
        result = AnalysisResult.create(
            patient_id=patient_id,
            analysis_type=data.get('analysis_type'),
            file_name=data.get('file_name'),
            audio_features=json.dumps(data.get('audio_features')) if data.get('audio_features') else None,
            predictions=json.dumps(data.get('predictions')) if data.get('predictions') else None,
            facial_expressions=json.dumps(data.get('facial_expressions')) if data.get('facial_expressions') else None,
            combined_analysis=json.dumps(data.get('combined_analysis')) if data.get('combined_analysis') else None,
            notes=data.get('notes')
        )
        
        if not result:
            return jsonify({'error': 'Failed to save analysis result'}), 500
        
        return jsonify({
            'success': True,
            'message': 'Analysis result saved successfully',
            'result': result
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/<patient_id>/analysis', methods=['GET'])
@token_required
def get_patient_analysis(patient_id):
    """Get all analysis results for a patient"""
    try:
        ensure_db()
        patient = Patient.get_by_id(patient_id)
        
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Verify patient belongs to current user
        if patient['user_id'] != request.user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Get limit from query parameters
        limit = request.args.get('limit', 10, type=int)
        results = AnalysisResult.get_latest_by_patient(patient_id, limit)
        
        return jsonify({
            'success': True,
            'patient_id': patient_id,
            'analysis_results': results,
            'total_count': len(results)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/<patient_id>/analysis/<result_id>', methods=['GET'])
@token_required
def get_analysis_detail(patient_id, result_id):
    """Get specific analysis result"""
    try:
        ensure_db()
        patient = Patient.get_by_id(patient_id)
        
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Verify patient belongs to current user
        if patient['user_id'] != request.user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        result = AnalysisResult.get_by_id(result_id)
        
        if not result or result['patient_id'] != patient_id:
            return jsonify({'error': 'Analysis result not found'}), 404
        
        # Parse JSON fields
        if result.get('audio_features'):
            result['audio_features'] = json.loads(result['audio_features'])
        if result.get('predictions'):
            result['predictions'] = json.loads(result['predictions'])
        if result.get('facial_expressions'):
            result['facial_expressions'] = json.loads(result['facial_expressions'])
        if result.get('combined_analysis'):
            result['combined_analysis'] = json.loads(result['combined_analysis'])
        
        return jsonify({
            'success': True,
            'result': result
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
