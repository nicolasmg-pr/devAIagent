import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  OneToMany,
} from 'typeorm';
import { ChecklistItem } from '../../checklists/entities/checklist-item.entity';

@Entity('rule_templates')
export class RuleTemplate {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ type: 'varchar', length: 20, name: 'rule_type' })
  rule_type: string;

  @Column({ type: 'varchar', length: 50 })
  category: string;

    @Column({ type: 'jsonb', name: 'condition_expression' })
  condition_expression: RuleCondition;

  @Column({ type: 'jsonb', name: 'output_parameters' })
  output_parameters: RuleOutputParams;

// Add to file:
export interface RuleCondition {
  zone?: string;
  length?: { min?: number; max?: number };
  passengers?: { min?: number; max?: number };
}

export interface RuleOutputParams {
  section: string;
  description: string;
  priority: number;
}

  @OneToMany(() => ChecklistItem, (item) => item.rule_template)
  checklist_items: ChecklistItem[];
}
