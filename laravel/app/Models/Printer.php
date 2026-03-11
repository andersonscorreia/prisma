<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Printer extends Model
{
    protected $fillable = [
        'serial_number',
        'name',
        'model',
        'ip_address',
        'last_counter',
        'last_toner_data',
        'status',
        'check_interval',
        'force_update',
    ];

    protected function casts(): array
    {
        return [
            'last_toner_data' => 'array',
            'force_update' => 'boolean',
        ];
    }
}
