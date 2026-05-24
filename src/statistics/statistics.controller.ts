import { Controller, Get, Query, UseGuards } from '@nestjs/common';
import { StatisticsService } from './statistics.service';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { CurrentUser } from '../auth/decorators/current-user.decorator';

@Controller('api/v1/statistics')
@UseGuards(JwtAuthGuard)
export class StatisticsController {
  constructor(private statisticsService: StatisticsService) {}

  @Get('monthly')
  async getMonthlyStats(
    @Query('month') month: number,
    @Query('year') year: number,
    @CurrentUser() userId: string,
  ) {
    return this.statisticsService.getMonthlyStats(userId, month, year);
  }
}