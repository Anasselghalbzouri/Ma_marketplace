<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('payouts', function (Blueprint $table) {
            $table->id();
            $table->bigInteger('seller_id')->unsigned()->nullable(false)->comment('Vendeur reçoit Reversement');
            $table->string('period_start', 255)->nullable(false);
            $table->string('ajout', 255)->nullable();
            $table->string('paid_on', 255)->nullable(false)->comment('date');
            $table->decimal('amount', 10, 2)->nullable(false);
            $table->string('method', 32)->nullable(false)->comment('mode : ModeReversement');
            $table->string('cash_proof', 255)->nullable()->comment('preuveRemise si espèces (HYPOTHÈSE F011)');
            $table->bigInteger('recorded_by_user_id')->unsigned()->nullable(false);
            $table->timestamps();
            $table->unique(['seller_id', 'period_start']);
            $table->index(['seller_id', 'paid_on']);
        });

        // Contraintes nommees et FULLTEXT (MySQL >= 8.0.16). Ignores sous SQLite.
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE payouts ADD CONSTRAINT fk_payouts_seller FOREIGN KEY (seller_id) REFERENCES sellers (id) ON DELETE RESTRICT");
            DB::statement("ALTER TABLE payouts ADD CONSTRAINT fk_payouts_recorder FOREIGN KEY (recorded_by_user_id) REFERENCES users (id) ON DELETE RESTRICT");
        }

        // Contraintes CHECK nommees (MySQL >= 8.0.16). Ignores sous SQLite (tests en memoire).
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE payouts ADD CONSTRAINT ck_payouts_amount CHECK (amount > 0)");
            DB::statement("ALTER TABLE payouts ADD CONSTRAINT ck_payouts_method CHECK (method IN ('bank_transfer', 'cash'))");
            DB::statement("ALTER TABLE payouts ADD CONSTRAINT ck_payouts_cash_proof CHECK (method <> 'cash' OR cash_proof IS NOT NULL)");
        }

    }

    public function down(): void
    {
        Schema::dropIfExists('payouts');
    }
};
