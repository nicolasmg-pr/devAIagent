import { Controller, Post, Put, Delete, Body, Param, Get, UseGuards } from '@nestjs/common';
import { BudgetService } from './budget.service';
import { CreateBudgetDto } from './dto/create-budget.dto';
import { UpdateBudgetDto } from './dto/update-budget.dto';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { CurrentUser } from '../auth/decorators/current-user.decorator';

@Controller('api/v1/budgets')
@UseGuards(JwtAuthGuard)
export class BudgetController {
  constructor(private budgetService: BudgetService) {}

  @Post()
  async create(@Body() dto: CreateBudgetDto, @CurrentUser() userId: string) {
    return this.budgetService.create(dto, userId);
  }

  @Put(':id')
  async update(@Param('id') id: string, @Body() dto: UpdateBudgetDto, @CurrentUser() userId: string) {
    await this.budgetService.update(id, dto, userId);
    return { id, status: 'updated' };
  }

  @Delete(':id')
  async remove(@Param('id') id: string, @CurrentUser() userId: string) {
    await this.budgetService.remove(id, userId);
    return { status: 'deleted' };
  }
}