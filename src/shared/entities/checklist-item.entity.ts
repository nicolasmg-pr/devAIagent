import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
  ManyToOne,
  JoinColumn,
} from 'typeorm';
import { ChecklistInstance } from './checklist-instance.entity';

@Entity('checklist_items')
export class ChecklistItem {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @ManyToOne(() => ChecklistInstance, (instance) => instance.items, {
    onDelete: 'CASCADE',
  })
  @JoinColumn({ name: 'instance_id' })
  instance: ChecklistInstance;

  @Column({ name: 'instance_id', type: 'uuid' })
  instance_id: string;

  @Column({ name: 'rule_category', type: 'varchar', length: 50 })
  rule_category: string;

  @Column({ type: 'text' })
  description: string;

  @Column({ name: 'is_completed', type: 'boolean', default: false })
  is_completed: boolean;

  @CreateDateColumn({
    name: 'last_updated',
    type: 'timestamp',
    default: () => 'CURRENT_TIMESTAMP',
  })
  last_updated: Date;
}