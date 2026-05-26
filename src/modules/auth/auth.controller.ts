import {
  Controller,
  Post,
  Body,
  UsePipes,
  ValidationPipe,
} from '@nestjs/common';
import { AuthService } from './auth.service';
import { LoginDto } from './dto/login.dto';

@Controller('auth')
export class AuthController {
  constructor(private readonly authService: AuthService) {}

  @Post('login')
  @UsePipes(new ValidationPipe({ whitelist: true, transform: true }))
  async login(@Body() loginDto: LoginDto) {
    const user = await this.authService.validateUser(
      loginDto.email,
      loginDto.password,
    );

    if (!user) {
      return {
        success: false,
        message: 'Invalid credentials',
      };
    }

    const token = await this.authService.generateToken(user as any);

    return {
      success: true,
      token,
      user,
    };
  }

  @Post('register')
  @UsePipes(new ValidationPipe({ whitelist: true, transform: true }))
  async register(@Body() loginDto: LoginDto) {
    const user = await this.authService.createOrUpdateUser(
      loginDto.email,
    );

    const token = await this.authService.generateToken(user);

    return {
      success: true,
      token,
      user,
    };
  }
}