<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class PrinterLocation extends Model
{
    protected $fillable = [
        'printer_id',
        'client_id',
        'installed_at',
        'removed_at',
    ];

    protected $casts = [
        'installed_at' => 'datetime',
        'removed_at' => 'datetime',
    ];

    public function printer()
    {
        return $this->belongsTo(Printer::class);
    }

    public function client()
    {
        return $this->belongsTo(Client::class);
    }
}
