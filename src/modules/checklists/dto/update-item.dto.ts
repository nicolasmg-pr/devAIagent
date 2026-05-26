import { IsBoolean } from 'class-validator';

export class UpdateChecklistItemDto {
  @IsBoolean()
  is_completed: boolean;
}