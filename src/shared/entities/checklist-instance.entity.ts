import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
  ManyToOne,
  OneToMany,
  JoinColumn,
} from 'typeorm';
import { Vessel } from './vessel.entity';
import { Protocol } from './protocol.entity';
import { User } from './user.entity';
import { ChecklistItem } from './checklist-item.entity';

export enum ChecklistStatusEnum {
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled',
}

@Entity('checklist_instances')
export class ChecklistInstance {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @ManyToOne(() => Vessel, (vessel) => vessel.checklists, {
    onDelete: 'CASCADE',
  })
  @JoinColumn({ name: 'vessel_id' })
  vessel: Vessel;

  @Column({ name: 'vessel_id', type: 'uuid' })
  vessel_id: string;

  @ManyToOne(() => Protocol, (protocol) => protocol.checklist_instances, {
    onDelete: 'SET NULL',
  })
  @JoinColumn({ name: 'protocol_id' })
  protocol: Protocol;

  @Column({ name: 'protocol_id', type: 'uuid', nullable: true })
  protocol_id: string;

  @ManyToOne(() => User, { onDelete: 'SET NULL', nullable: true })
  @JoinColumn({ name: 'user_id' })
  user: User;

  @Column({ name: 'user_id', type: 'uuid', nullable: true })
  user_id: string;

  @Column({
    type: 'enum',
    enum: ChecklistStatusEnum,
    default: ChecklistStatusEnum.PENDING,
  })
  status: ChecklistStatusEnum;

  @CreateDateColumn({ type: 'timestamp', default: () => 'CURRENT_TIMESTAMP' })
  created_at: Date;

  @UpdateDateColumn({ type: 'timestamp', default: () => 'CURRENT_TIMESTAMP' })
  updated_at: Date;

  @OneToMany(() => ChecklistItem, (item) => item.instance, {
    cascade: true,
  })
  items: ChecklistItem[];
}