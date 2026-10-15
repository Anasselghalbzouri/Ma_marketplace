<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('users', function (Blueprint $table) {
            $table->id();
            $table->string('phone', 20)->nullable(false);
            $table->string('format', 255)->nullable();
            $table->string('password', 255)->nullable(false)->comment('Hash uniquement ; jamais renvoyé (FR-054)');
            $table->string('role', 32)->nullable(false);
            $table->timestamp('last_login_at')->nullable();
            $table->timestamps();
            $table->unique('phone');
            $table->index('role');
        });

        // Contraintes CHECK nommees (MySQL >= 8.0.16). Ignores sous SQLite (tests en memoire).
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE users ADD CONSTRAINT ck_users_role CHECK (role IN ('customer', 'seller', 'admin'))");
        }

    }

    public function down(): void
    {
        Schema::dropIfExists('users');
    }
};
