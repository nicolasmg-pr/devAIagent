import 'package:dartz/dartz.dart';
import '../../../core/errors/failures.dart';
import '../../../core/network/dio_client.dart';
import '../entities/stat_entities.dart';
import '../repositories/stats_repository.dart';

class StatsRepositoryImpl implements StatsRepository {
  final DioClient dioClient;

  StatsRepositoryImpl(this.dioClient);

  @override
  Future<Either<Failure, StatsResponse>> getMonthlyStats({
    int? month,
    int? year,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (month != null) queryParams['month'] = month;
      if (year != null) queryParams['year'] = year;

      final response = await dioClient.get<Map<String, dynamic>>(
        '/api/v1/stats/monthly',
        queryParameters: queryParams,
      );
      return Right(StatsResponse.fromJson(response as Map<String, dynamic>));
    } catch (e) {
      return Left(ServerFailure(message: e.toString()));
    }
  }
}
