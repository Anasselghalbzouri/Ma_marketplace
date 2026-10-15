<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('shops', function (Blueprint $table) {
            $table->id();
            $table->bigInteger('seller_id')->unsigned()->nullable(false);
            $table->string('name', 150)->nullable(false);
            $table->text('description')->nullable();
            $table->string('pickup_address', 500)->nullable(false);
            $table->timestamps();
            $table->unique('seller_id');
        });

        // Contraintes nommees et FULLTEXT (MySQL >= 8.0.16). Ignores sous SQLite.
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE shops ADD CONSTRAINT fk_shops_seller FOREIGN KEY (seller_id) REFERENCES sellers (id) ON DELETE RESTRICT");
        }

    }

    public function down(): void
    {
        Schema::dropIfExists('shops');
    }
};
