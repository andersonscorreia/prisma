<?php

use Illuminate\Support\Facades\Route;
use Laravel\Fortify\Features;

Route::inertia('/', 'Welcome', [
    'canRegister' => Features::enabled(Features::registration()),
])->name('home');

Route::get('dashboard', [\App\Http\Controllers\PrinterController::class, 'index'])->name('dashboard');
Route::get('dashboard/reports', [\App\Http\Controllers\ReportController::class, 'index'])->name('reports.index');
Route::post('dashboard/printers/{printer}/config', [\App\Http\Controllers\PrinterController::class, 'updateConfig'])->name('printers.config');
Route::post('dashboard/printers/{printer}/assign-client', [\App\Http\Controllers\PrinterController::class, 'assignClient'])->name('printers.assign_client');

Route::get('dashboard/clients', [\App\Http\Controllers\ClientController::class, 'index'])->name('clients.index');
Route::post('dashboard/clients', [\App\Http\Controllers\ClientController::class, 'store'])->name('clients.store');
Route::delete('dashboard/clients/{client}', [\App\Http\Controllers\ClientController::class, 'destroy'])->name('clients.destroy');

require __DIR__.'/settings.php';
