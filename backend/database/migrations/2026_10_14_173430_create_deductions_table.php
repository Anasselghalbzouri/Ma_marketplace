<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('deductions', function (Blueprint $table) {
            $table->id();
            $table->bigInteger('product_return_id')->unsigned()->nullable(false)->comment('Retour donne lieu à');
            $table->bigInteger('seller_id')->unsigned()->nullable(false)->comment('dupliqué pour le calcul hebdomadaire');
            $table->decimal('amount', 10, 2)->nullable(false);
            $table->string('origin', 32)->nullable(false)->comment('origine : remboursement | fraisDeRetour');
            $table->string('deducted_on', 255)->nullable(false)->comment('date');
            $table->bigInteger('payout_id')->unsigned()->nullable()->comment('régularisée sur Reversement 0..1');
            $table->timestamps();
            $table->unique(['product_return_id', 'origin']);
            $table->index(['seller_id', 'payout_id']);
            $table->index('payout_id');
        });

        // Contraintes nommees et FULLTEXT (MySQL >= 8.0.16). Ignores sous SQLite.
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE deductions ADD CONSTRAINT fk_deductions_return FOREIGN KEY (product_return_id) REFERENCES product_returns (id) ON DELETE RESTRICT");
            DB::statement("ALTER TABLE deductions ADD CONSTRAINT fk_deductions_seller FOREIGN KEY (seller_id) REFERENCES sellers (id) ON DELETE RESTRICT");
            DB::statement("ALTER TABLE deductions ADD CONSTRAINT fk_deductions_payout FOREIGN KEY (payout_id) REFERENCES payouts (id) ON DELETE RESTRICT");
        }

        // Contraintes CHECK nommees (MySQL >= 8.0.16). Ignores sous SQLite (tests en memoire).
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE deductions ADD CONSTRAINT ck_deductions_amount CHECK (amount > 0)");
            DB::statement("ALTER TABLE deductions ADD CONSTRAINT ck_deductions_origin CHECK (origin IN ('refund', 'return_fee'))");
        }

    }

    public function down(): void
    {
        Schema::dropIfExists('deductions');
    }
};
