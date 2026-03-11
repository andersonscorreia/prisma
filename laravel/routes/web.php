<?php

use Illuminate\Support\Facades\Route;
use Laravel\Fortify\Features;

Route::inertia('/', 'Welcome', [
    'canRegister' => Features::enabled(Features::registration()),
])->name('home');

Route::get('dashboard', [\App\Http\Controllers\PrinterController::class, 'index'])->name('dashboard');
Route::post('dashboard/printers/{printer}/config', [\App\Http\Controllers\PrinterController::class, 'updateConfig'])->name('printers.config');

require __DIR__.'/settings.php';
