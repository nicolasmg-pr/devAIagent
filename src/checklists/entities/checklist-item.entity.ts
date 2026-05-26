import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  ManyToOne,
  JoinColumn,
} from 'typeorm';
import { Checklist } from './checklist.entity';
import { RuleTemplate } from '../../rules/entities/rule-template.entity';

@Entity('checklist_items')
export class ChecklistItem {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ type: 'uuid', name: 'checklist_id' })
  checklist_id: string;

  @ManyToOne(() => Checklist, (checklist) => checklist.items, { nullable: false })
  @JoinColumn({ name: 'checklist_id' })
  checklist: Checklist;

  @Column({ type: 'varchar', length: 50 })
  section: string;

  @Column({ type: 'text' })
  description: string;

  @Column({ type: 'boolean', default: false, name: 'is_completed' })
  is_completed: boolean;

  @Column({ type: 'text', nullable: true, name: 'custom_notes' })
  custom_notes: string;

  @Column({ type: 'uuid', nullable: true, name: 'rule_trigger_id' })
  rule_trigger_id: string;

  @ManyToOne(() => RuleTemplate, { nullable: true })
  @JoinColumn({ name: 'rule_trigger_id' })
  rule_template: RuleTemplate;
}
