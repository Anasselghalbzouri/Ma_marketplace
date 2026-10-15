<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('cash_discrepancies', function (Blueprint $table) {
            $table->id();
            $table->bigInteger('order_id')->unsigned()->nullable(false);
            $table->decimal('amount', 10, 2)->nullable(false);
            $table->string('recorded_on', 255)->nullable(false)->comment('date');
            $table->bigInteger('recorded_by_user_id')->unsigned()->nullable();
            $table->timestamps();
            $table->unique('order_id');
        });

        // Contraintes nommees et FULLTEXT (MySQL >= 8.0.16). Ignores sous SQLite.
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE cash_discrepancies ADD CONSTRAINT fk_cash_discrepancies_order FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE RESTRICT");
            DB::statement("ALTER TABLE cash_discrepancies ADD CONSTRAINT fk_cash_discrepancies_recorder FOREIGN KEY (recorded_by_user_id) REFERENCES users (id) ON DELETE RESTRICT");
        }

        // Contraintes CHECK nommees (MySQL >= 8.0.16). Ignores sous SQLite (tests en memoire).
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE cash_discrepancies ADD CONSTRAINT ck_cash_discrepancies_amount CHECK (amount <> 0)");
        }

    }

    public function down(): void
    {
        Schema::dropIfExists('cash_discrepancies');
    }
};
