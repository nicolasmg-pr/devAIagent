import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { Checklist } from './entities/checklist.entity';
import { ChecklistItem } from './entities/checklist-item.entity';
import { ChecklistsService } from './checklists.service';
import { ChecklistsController } from './checklists.controller';
import { VesselsModule } from '../vessels/vessels.module';

@Module({
  imports: [TypeOrmModule.forFeature([Checklist, ChecklistItem]), VesselsModule],
  controllers: [ChecklistsController],
  providers: [ChecklistsService],
  exports: [ChecklistsService],
})
export class ChecklistsModule {}
