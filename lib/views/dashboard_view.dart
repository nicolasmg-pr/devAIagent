import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/expense_provider.dart';
import 'add_expense_view.dart';

class DashboardView extends StatelessWidget {
  const DashboardView({super.key});

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<ExpenseProvider>();
    
    WidgetsBinding.instance.addPostFrameCallback((_) {
      provider.fetchExpenses();
    });

    return Scaffold(
      appBar: AppBar(title: const Text('Mis Gastos')),
      body: provider.expenses.isEmpty
          ? const Center(child: Text('No hay gastos'))
          : ListView.builder(
              itemCount: provider.expenses.length,
              itemBuilder: (context, index) {
                final expense = provider.expenses[index];
                return ListTile(
                  title: Text(expense.description),
                  subtitle: Text(expense.date),
                  trailing: Text('\$${expense.amount}'),
                  onLongPress: () {
                    provider.deleteExpense(expense.id);
                  },
                );
              },
            ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => const AddExpenseView()),
          );
        },
        child: const Icon(Icons.add),
      ),
    );
  }
}