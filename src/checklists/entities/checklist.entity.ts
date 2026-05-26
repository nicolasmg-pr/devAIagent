import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  ManyToOne,
  OneToMany,
  JoinColumn,
} from 'typeorm';
import { Vessel } from '../../vessels/entities/vessel.entity';
import { ChecklistItem } from './checklist-item.entity';

export enum ChecklistStatus {
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETED = 'COMPLETED',
  CANCELLED = 'CANCELLED',
}

@Entity('checklists')
export class Checklist {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ type: 'uuid', name: 'vessel_id' })
  vessel_id: string;

  @ManyToOne(() => Vessel, (vessel) => vessel.checklists, { nullable: false })
  @JoinColumn({ name: 'vessel_id' })
  vessel: Vessel;

  @CreateDateColumn({ name: 'generated_at', type: 'timestamp' })
  generated_at: Date;

  @Column({ type: 'varchar', length: 20, default: ChecklistStatus.IN_PROGRESS })
  status: ChecklistStatus;

  @Column({ type: 'varchar', length: 255, nullable: true, name: 'export_reference' })
  export_reference: string;

  @OneToMany(() => ChecklistItem, (item) => item.checklist)
  items: ChecklistItem[];
}
