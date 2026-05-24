import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { Expense } from '../expenses/expense.entity';
import { StatisticsController } from './statistics.controller';
import { StatisticsService } from './statistics.service';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';

@Module({
  imports: [TypeOrmModule.forFeature([Expense])],
  controllers: [StatisticsController],
  providers: [StatisticsService, JwtAuthGuard],
  exports: [StatisticsService],
})
export class StatisticsModule {}