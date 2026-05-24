import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../features/auth/presentation/screens/login_screen.dart';
import '../../features/auth/presentation/screens/register_screen.dart';
import '../../features/expenses/presentation/screens/dashboard_screen.dart';
import '../../features/expenses/presentation/screens/expenses_history_screen.dart';
import '../../features/expenses/presentation/screens/new_expense_screen.dart';
import '../../features/expenses/presentation/screens/expense_detail_screen.dart';
import '../../features/statistics/presentation/screens/statistics_screen.dart';
import '../../features/budgets/presentation/screens/budgets_screen.dart';
import '../../features/settings/presentation/screens/settings_screen.dart';
import '../../shared/services/storage_service.dart';

final GoRouter router = GoRouter(
  initialLocation: '/login',
  refreshListenable: StorageService.instance,
  routes: [
    // Auth Routes
    GoRoute(
      path: '/login',
      name: 'login',
      builder: (context, state) => const LoginScreen(),
    ),
    GoRoute(
      path: '/register',
      name: 'register',
      builder: (context, state) => const RegisterScreen(),
    ),
    
    // Main Routes (with Bottom Navigation)
    GoRoute(
      path: '/home',
      name: 'home',
      builder: (context, state) => const DashboardScreen(),
    ),
    GoRoute(
      path: '/expenses',
      name: 'expenses',
      builder: (context, state) => const ExpensesHistoryScreen(),
    ),
    GoRoute(
      path: '/expenses/new',
      name: 'new-expense',
      builder: (context, state) => const NewExpenseScreen(),
    ),
    GoRoute(
      path: '/expenses/:id',
      name: 'expense-detail',
      builder: (context, state) {
        final id = state.pathParameters['id']!;
        return ExpenseDetailScreen(expenseId: id);
      },
    ),
    GoRoute(
      path: '/statistics',
      name: 'statistics',
      builder: (context, state) => const StatisticsScreen(),
    ),
    GoRoute(
      path: '/budgets',
      name: 'budgets',
      builder: (context, state) => const BudgetsScreen(),
    ),
    GoRoute(
      path: '/settings',
      name: 'settings',
      builder: (context, state) => const SettingsScreen(),
    ),
  ],
  errorBuilder: (context, state) => Scaffold(
    body: Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.error_outline, size: 64, color: Colors.grey),
          const SizedBox(height: 16),
          Text(
            'Página no encontrada',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 8),
          Text(
            'La ruta solicitada no existe',
            style: Theme.of(context).textTheme.bodyMedium,
          ),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: () => router.go('/home'),
            child: const Text('Ir al Inicio'),
          ),
        ],
      ),
    ),
  ),
);
