import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { User } from '../shared/entities/user.entity';

export interface AuthPayload {
  id: string;
  email: string;
  iat: number;
  exp: number;
}

@Injectable()
export class AuthService {
  constructor(
    @InjectRepository(User)
    private readonly usersRepository: Repository<User>,
  ) {}

  async validateUser(
    email: string,
    password: string,
  ): Promise<User | null> {
    const user = await this.usersRepository.findOne({
      where: { email },
    });

    if (user && this.verifyPassword(password, user as any)) {
      const { password: _, ...result } = user as any;
      return result;
    }

    return null;
  }

  async findByEmail(email: string): Promise<User | null> {
    return this.usersRepository.findOne({
      where: { email },
    });
  }

  async createOrUpdateUser(
    email: string,
  ): Promise<User> {
    let user = await this.usersRepository.findOne({
      where: { email },
    });

    if (!user) {
      user = this.usersRepository.create({ email });
      await this.usersRepository.save(user);
    }

    return user;
  }

  private verifyPassword(
    password: string,
    user: any,
  ): boolean {
    if (!user.password) return true;
    return password === user.password;
  }

  async generateToken(user: User): Promise<AuthPayload> {
    return {
      id: user.id,
      email: user.email,
      iat: Math.floor(Date.now() / 1000),
      exp: Math.floor(Date.now() / 1000) + 3600,
    };
  }
}