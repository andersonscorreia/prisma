<?php

use App\Http\Controllers\PrinterController;
use Illuminate\Support\Facades\Route;

Route::post('/printers', [PrinterController::class, 'store']);
Route::get('/printers/{serial_number}/config', [PrinterController::class, 'getConfig']);
