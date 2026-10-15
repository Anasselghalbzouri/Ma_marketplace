<?php

namespace Tests\Feature;

use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\DB;
use Tests\TestCase;

class MigrationSeedTest extends TestCase
{
    use RefreshDatabase;

    /**
     * T-005 : migrations applied, rollbacked and re-applied without errors on empty SQLite DB.
     */
    public function test_migrations_can_be_rollbacked_and_reapplied(): void
    {
        $this->artisan('migrate:rollback', ['--force' => true])->assertSuccessful();
        $this->artisan('migrate', ['--force' => true])->assertSuccessful();

        $this->assertTrue(DB::getSchemaBuilder()->hasTable('users'));
        $this->assertTrue(DB::getSchemaBuilder()->hasTable('served_cities'));
        $this->assertTrue(DB::getSchemaBuilder()->hasTable('products'));
    }

    /**
     * T-005 : seeders insert Tanger and initial admin user.
     */
    public function test_reference_seeds_are_present(): void
    {
        $this->artisan('db:seed', ['--force' => true])->assertSuccessful();

        $this->assertDatabaseHas('served_cities', ['name' => 'Tanger']);
        $this->assertDatabaseHas('users', ['role' => 'admin']);
    }
}
