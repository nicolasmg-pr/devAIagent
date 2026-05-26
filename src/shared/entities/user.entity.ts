import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  OneToMany,
} from 'typeorm';
import { Vessel } from './vessel.entity';
import { ChecklistInstance } from './checklist-instance.entity';

@Entity('users')
export class User {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ type: 'varchar', length: 255, unique: true })
  email: string;

  @CreateDateColumn({ type: 'timestamp', default: () => 'CURRENT_TIMESTAMP' })
  created_at: Date;

  @OneToMany(() => Vessel, (vessel) => vessel.user)
  vessels: Vessel[];

  @OneToMany(() => ChecklistInstance, (checklist) => checklist.user)
  checklists: ChecklistInstance[];
}