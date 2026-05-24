import { Controller, Get, Post, Put, Delete, Body, Param, Query, UseGuards } from '@nestjs/common';
import { ExpenseService } from './expense.service';
import { CreateExpenseDto } from './dto/create-expense.dto';
import { UpdateExpenseDto } from './dto/update-expense.dto';
import { QueryExpenseDto } from './dto/query-expense.dto';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { CurrentUser } from '../auth/decorators/current-user.decorator';

@Controller('api/v1/expenses')
@UseGuards(JwtAuthGuard)
export class ExpenseController {
  constructor(private expenseService: ExpenseService) {}

  @Post()
  async create(@Body() dto: CreateExpenseDto, @CurrentUser() userId: string) {
    return this.expenseService.create(dto, userId);
  }

  @Get()
  async findAll(@Query() query: QueryExpenseDto, @CurrentUser() userId: string) {
    return this.expenseService.findAll(query, userId);
  }

  @Put(':id')
  async update(@Param('id') id: string, @Body() dto: UpdateExpenseDto, @CurrentUser() userId: string) {
    await this.expenseService.update(id, dto, userId);
    return { id, status: 'updated' };
  }

  @Delete(':id')
  async remove(@Param('id') id: string, @CurrentUser() userId: string) {
    await this.expenseService.remove(id, userId);
    return { status: 'deleted' };
  }
}