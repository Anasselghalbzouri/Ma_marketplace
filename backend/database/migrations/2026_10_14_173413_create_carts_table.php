<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('carts', function (Blueprint $table) {
            $table->id();
            $table->bigInteger('customer_id')->unsigned()->nullable();
            $table->char('guest_token_hash', 64)->nullable()->comment('SHA-256 du jeton de panier visiteur ; jamais le jeton en clair');
            $table->timestamps();
            $table->unique('customer_id');
            $table->unique('guest_token_hash');
        });

        // Contraintes nommees et FULLTEXT (MySQL >= 8.0.16). Ignores sous SQLite.
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE carts ADD CONSTRAINT fk_carts_customer FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE RESTRICT");
        }

        // Contraintes CHECK nommees (MySQL >= 8.0.16). Ignores sous SQLite (tests en memoire).
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE carts ADD CONSTRAINT ck_carts_owner CHECK (customer_id IS NOT NULL OR guest_token_hash IS NOT NULL)");
        }

    }

    public function down(): void
    {
        Schema::dropIfExists('carts');
    }
};
