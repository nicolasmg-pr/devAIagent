import { IsNumber, IsDateString, IsString, IsOptional, IsUUID } from 'class-validator';

export class UpdateExpenseDto {
  @IsUUID()
  @IsOptional()
  categoryId?: string;

  @IsNumber()
  @IsOptional()
  amount?: number;

  @IsDateString()
  @IsOptional()
  date?: string;

  @IsString()
  @IsOptional()
  description?: string;
}