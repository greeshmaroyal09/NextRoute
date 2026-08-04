import os
import shutil

CORE_API_CLIENT = '''import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';

class ApiClient {
  final Dio _dio;

  ApiClient() : _dio = Dio(BaseOptions(
    baseUrl: 'http://10.0.2.2:8000/api/v1',
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 10),
  )) {
    _dio.interceptors.add(LogInterceptor(responseBody: true, requestBody: true));
  }

  Future<Response> get(String path, {Map<String, dynamic>? queryParameters}) async {
    try {
      return await _dio.get(path, queryParameters: queryParameters);
    } catch (e) {
      debugPrint('GET Error: $e');
      rethrow;
    }
  }

  Future<Response> post(String path, {dynamic data}) async {
    try {
      return await _dio.post(path, data: data);
    } catch (e) {
      debugPrint('POST Error: $e');
      rethrow;
    }
  }
}
'''

DOMAIN_MODELS = '''class StationInfo {
  final String code;
  final String name;
  final String type;
  
  StationInfo({required this.code, required this.name, required this.type});
  
  factory StationInfo.fromJson(Map<String, dynamic> json) {
    return StationInfo(
      code: json['code'] ?? '',
      name: json['name'] ?? '',
      type: json['type'] ?? 'UNKNOWN',
    );
  }
}

class JourneySegment {
  final String segmentType;
  final StationInfo origin;
  final StationInfo destination;
  final String departureTime;
  final String arrivalTime;
  final int durationMins;
  final double distanceKm;
  final String? vehicleName;
  final double totalFare;

  JourneySegment({
    required this.segmentType, required this.origin, required this.destination,
    required this.departureTime, required this.arrivalTime, required this.durationMins,
    required this.distanceKm, this.vehicleName, required this.totalFare
  });

  factory JourneySegment.fromJson(Map<String, dynamic> json) {
    return JourneySegment(
      segmentType: json['segment_type'] ?? 'TRAIN',
      origin: StationInfo.fromJson(json['origin'] ?? {}),
      destination: StationInfo.fromJson(json['destination'] ?? {}),
      departureTime: json['departure_time'] ?? '',
      arrivalTime: json['arrival_time'] ?? '',
      durationMins: json['duration_mins'] ?? 0,
      distanceKm: (json['distance_km'] ?? 0).toDouble(),
      vehicleName: json['vehicle_info']?['name'],
      totalFare: (json['cost']?['total_fare'] ?? 0).toDouble(),
    );
  }
}

class JourneyResponse {
  final String journeyId;
  final List<JourneySegment> segments;
  final int totalDurationMins;
  final double totalCost;
  final int totalTransfers;
  final double overallScore;
  final List<String> badges;
  final String recommendationSentence;

  JourneyResponse({
    required this.journeyId, required this.segments, required this.totalDurationMins,
    required this.totalCost, required this.totalTransfers, required this.overallScore,
    required this.badges, required this.recommendationSentence
  });

  factory JourneyResponse.fromJson(Map<String, dynamic> json) {
    var segList = json['segments'] as List? ?? [];
    return JourneyResponse(
      journeyId: json['journey_id'] ?? '',
      segments: segList.map((e) => JourneySegment.fromJson(e)).toList(),
      totalDurationMins: json['total_duration_mins'] ?? 0,
      totalCost: (json['total_cost']?['total_fare'] ?? 0).toDouble(),
      totalTransfers: json['total_transfers'] ?? 0,
      overallScore: (json['score']?['overall_score'] ?? 0).toDouble(),
      badges: List<String>.from(json['badges'] ?? []),
      recommendationSentence: json['recommendation_sentence'] ?? '',
    );
  }
}
'''

def write_core():
    os.makedirs('lib/core/network', exist_ok=True)
    os.makedirs('lib/shared/domain/models', exist_ok=True)
    
    with open('lib/core/network/api_client.dart', 'w', encoding='utf-8') as f:
        f.write(CORE_API_CLIENT)
    
    with open('lib/shared/domain/models/models.dart', 'w', encoding='utf-8') as f:
        f.write(DOMAIN_MODELS)
    
    print("Core written.")

if __name__ == '__main__':
    write_core()
