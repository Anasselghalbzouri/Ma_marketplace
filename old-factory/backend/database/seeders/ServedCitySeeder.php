<?php

namespace Database\Seeders;

use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;

class ServedCitySeeder extends Seeder
{
    use WithoutModelEvents;

    /**
     * Seed the initial served city (RG-001 : Tanger).
     */
    public function run(): void
    {
        DB::table('served_cities')->insertOrIgnore([
            'name' => 'Tanger',
            'created_at' => now(),
            'updated_at' => now(),
        ]);
    }
}
