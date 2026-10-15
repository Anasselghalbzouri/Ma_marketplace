<?php

namespace Database\Seeders;

use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;

class AdminUserSeeder extends Seeder
{
    use WithoutModelEvents;

    /**
     * Seed the initial administrator account.
     *
     * Credentials must be overridden via environment before production use.
     */
    public function run(): void
    {
        DB::table('users')->insertOrIgnore([
            'phone' => env('ADMIN_INITIAL_PHONE', '+212600000000'),
            'password' => Hash::make(env('ADMIN_INITIAL_PASSWORD', 'changeme')),
            'role' => 'admin',
            'created_at' => now(),
            'updated_at' => now(),
        ]);
    }
}
