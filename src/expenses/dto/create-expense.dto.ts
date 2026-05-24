import { IsNumber, IsDateString, IsString, IsOptional, IsUUID } from 'class-validator';

export class CreateExpenseDto {
  @IsUUID()
  categoryId: string;

  @IsNumber()
  amount: number;

  @IsDateString()
  date: string;

  @IsString()
  @IsOptional()
  description?: string;
}