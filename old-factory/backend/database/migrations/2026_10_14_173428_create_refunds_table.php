<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('refunds', function (Blueprint $table) {
            $table->id();
            $table->bigInteger('product_return_id')->unsigned()->nullable(false);
            $table->decimal('amount', 10, 2)->nullable(false)->comment('prix − frais si changement d\'avis (RG-022)');
            $table->string('method', 32)->nullable(false)->comment('moyen : MoyenRemboursement');
            $table->string('reference', 100)->nullable(false)->comment('référence de l\'opération traçable');
            $table->string('refunded_on', 255)->nullable(false)->comment('date');
            $table->bigInteger('recorded_by_user_id')->unsigned()->nullable(false);
            $table->timestamps();
            $table->unique('product_return_id');
        });

        // Contraintes nommees et FULLTEXT (MySQL >= 8.0.16). Ignores sous SQLite.
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE refunds ADD CONSTRAINT fk_refunds_return FOREIGN KEY (product_return_id) REFERENCES product_returns (id) ON DELETE RESTRICT");
            DB::statement("ALTER TABLE refunds ADD CONSTRAINT fk_refunds_recorder FOREIGN KEY (recorded_by_user_id) REFERENCES users (id) ON DELETE RESTRICT");
        }

        // Contraintes CHECK nommees (MySQL >= 8.0.16). Ignores sous SQLite (tests en memoire).
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE refunds ADD CONSTRAINT ck_refunds_amount CHECK (amount >= 0)");
            DB::statement("ALTER TABLE refunds ADD CONSTRAINT ck_refunds_method CHECK (method IN ('bank_transfer', 'other_traceable'))");
        }

    }

    public function down(): void
    {
        Schema::dropIfExists('refunds');
    }
};
