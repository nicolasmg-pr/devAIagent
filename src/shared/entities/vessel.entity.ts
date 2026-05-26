import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  ManyToOne,
  OneToMany,
  JoinColumn,
} from 'typeorm';
import { User } from './user.entity';
import { ChecklistInstance } from './checklist-instance.entity';

export enum ZoneEnum {
  COASTAL = 'coastal',
  OFFSHORE = 'offshore',
  LIMITED = 'limited',
  UNLIMITED = 'unlimited',
}

export enum PropulsionEnum {
  DIESEL = 'diesel',
  GASOLINE = 'gasoline',
  ELECTRIC = 'electric',
  HYBRID = 'hybrid',
  SAIL = 'sail',
}

@Entity('vessels')
export class Vessel {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @ManyToOne(() => User, (user) => user.vessels, { onDelete: 'CASCADE' })
  @JoinColumn({ name: 'user_id' })
  user: User;

  @Column({ name: 'user_id', type: 'uuid' })
  user_id: string;

  @Column({ type: 'varchar', length: 100 })
  name: string;

  @Column({ type: 'decimal', precision: 4, scale: 2 })
  length: number;

  @Column({ type: 'int' })
  capacity: number;

  @Column({
    type: 'enum',
    enum: ZoneEnum,
    default: ZoneEnum.COASTAL,
  })
  zone: ZoneEnum;

  @Column({
    type: 'enum',
    enum: PropulsionEnum,
    default: PropulsionEnum.DIESEL,
  })
  propulsion: PropulsionEnum;

  @CreateDateColumn({ type: 'timestamp', default: () => 'CURRENT_TIMESTAMP' })
  created_at: Date;

  @OneToMany(() => ChecklistInstance, (checklist) => checklist.vessel)
  checklists: ChecklistInstance[];
}