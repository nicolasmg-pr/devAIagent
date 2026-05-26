import { IsUUID, IsBoolean, IsOptional, IsString } from 'class-validator';

export class UpdateItemDto {
  @IsUUID('4', { message: 'Item ID must be a valid UUID' })
  item_id: string;

  @IsBoolean({ message: 'is_completed must be a boolean' })
  is_completed: boolean;

  @IsString()
  @IsOptional()
  custom_notes?: string;
}
