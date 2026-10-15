<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('return_disputes', function (Blueprint $table) {
            $table->id();
            $table->bigInteger('product_return_id')->unsigned()->nullable(false);
            $table->timestamp('opened_at')->nullable(false);
            $table->string('decision', 32)->nullable()->comment('décision (STATE-003 t7/t8) — écart E-08');
            $table->string('decision_reason', 1000)->nullable();
            $table->decimal('refunded_amount', 10, 2)->nullable()->comment('montantRemboursé fixé par la décision');
            $table->string('fee_charged_to', 32)->nullable()->comment('imputationFrais : ImputationFrais');
            $table->timestamp('decided_at')->nullable()->comment('date');
            $table->bigInteger('decided_by_user_id')->unsigned()->nullable();
            $table->timestamps();
            $table->unique('product_return_id');
            $table->index('decided_at');
        });

        // Contraintes nommees et FULLTEXT (MySQL >= 8.0.16). Ignores sous SQLite.
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE return_disputes ADD CONSTRAINT fk_return_disputes_return FOREIGN KEY (product_return_id) REFERENCES product_returns (id) ON DELETE RESTRICT");
            DB::statement("ALTER TABLE return_disputes ADD CONSTRAINT fk_return_disputes_decider FOREIGN KEY (decided_by_user_id) REFERENCES users (id) ON DELETE RESTRICT");
        }

        // Contraintes CHECK nommees (MySQL >= 8.0.16). Ignores sous SQLite (tests en memoire).
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE return_disputes ADD CONSTRAINT ck_return_disputes_decision CHECK (decision IS NULL OR decision IN ('in_favor_of_customer', 'in_favor_of_seller'))");
            DB::statement("ALTER TABLE return_disputes ADD CONSTRAINT ck_return_disputes_fee CHECK (fee_charged_to IS NULL OR fee_charged_to IN ('customer', 'seller'))");
            DB::statement("ALTER TABLE return_disputes ADD CONSTRAINT ck_return_disputes_amount CHECK (refunded_amount IS NULL OR refunded_amount >= 0)");
            DB::statement("ALTER TABLE return_disputes ADD CONSTRAINT ck_return_disputes_decided CHECK ((decision IS NULL AND decided_at IS NULL AND decided_by_user_id IS NULL) OR (decision IS NOT NULL AND decided_at IS NOT NULL AND decided_by_user_id IS NOT NULL AND refunded_amount IS NOT NULL))");
        }

    }

    public function down(): void
    {
        Schema::dropIfExists('return_disputes');
    }
};
