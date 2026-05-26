import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
  OneToMany,
} from 'typeorm';
import { ChecklistInstance } from './checklist-instance.entity';

@Entity('protocols')
export class Protocol {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ type: 'varchar', length: 20, unique: true })
  version: string;

  @Column({ name: 'effective_date', type: 'date' })
  effective_date: Date;

  @Column({ name: 'rules_payload', type: 'jsonb', default: '{}' })
  rules_payload: Record<string, any>;

  @Column({ name: 'is_active', type: 'boolean', default: true })
  is_active: boolean;

  @CreateDateColumn({ type: 'timestamp', default: () => 'CURRENT_TIMESTAMP' })
  created_at: Date;

  @UpdateDateColumn({ type: 'timestamp', default: () => 'CURRENT_TIMESTAMP' })
  updated_at: Date;

  @OneToMany(() => ChecklistInstance, (checklist) => checklist.protocol)
  checklist_instances: ChecklistInstance[];
}