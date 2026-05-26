import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ChecklistInstance } from '../../shared/entities/checklist-instance.entity';
import { ChecklistItem } from '../../shared/entities/checklist-item.entity';
import { Vessel } from '../../shared/entities/vessel.entity';
import { Protocol } from '../../shared/entities/protocol.entity';
import { ChecklistsController } from './checklists.controller';
import { ChecklistsService } from './checklists.service';

@Module({
  imports: [
    TypeOrmModule.forFeature([
      ChecklistInstance,
      ChecklistItem,
      Vessel,
      Protocol,
    ]),
  ],
  controllers: [ChecklistsController],
  providers: [ChecklistsService],
  exports: [ChecklistsService],
})
export class ChecklistsModule {}