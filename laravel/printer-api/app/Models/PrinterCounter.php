<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class PrinterCounter extends Model
{
    protected $fillable = [
        'printer_id',
        'counter',
        'recorded_at',
    ];

    protected $casts = [
        'recorded_at' => 'datetime',
        'counter' => 'integer',
    ];

    public function printer()
    {
        return $this->belongsTo(Printer::class);
    }
}
