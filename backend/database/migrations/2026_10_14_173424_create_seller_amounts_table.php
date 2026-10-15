<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('seller_amounts', function (Blueprint $table) {
            $table->id();
            $table->bigInteger('order_line_id')->unsigned()->nullable(false);
            $table->bigInteger('seller_id')->unsigned()->nullable(false);
            $table->decimal('amount', 10, 2)->nullable(false);
            $table->string('sans', 255)->nullable();
            $table->string('status', 32)->nullable(false)->default('held');
            $table->timestamp('hold_until')->nullable(false);
            $table->string('figée', 255)->nullable();
            $table->bigInteger('payout_id')->unsigned()->nullable()->comment('inclus dans Reversement 0..1');
            $table->timestamps();
            $table->unique('order_line_id');
            $table->index(['seller_id', 'status']);
            $table->index(['status', 'hold_until']);
            $table->index('payout_id');
        });

        // Contraintes nommees et FULLTEXT (MySQL >= 8.0.16). Ignores sous SQLite.
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE seller_amounts ADD CONSTRAINT fk_seller_amounts_order_line FOREIGN KEY (order_line_id) REFERENCES order_lines (id) ON DELETE RESTRICT");
            DB::statement("ALTER TABLE seller_amounts ADD CONSTRAINT fk_seller_amounts_seller FOREIGN KEY (seller_id) REFERENCES sellers (id) ON DELETE RESTRICT");
            DB::statement("ALTER TABLE seller_amounts ADD CONSTRAINT fk_seller_amounts_payout FOREIGN KEY (payout_id) REFERENCES payouts (id) ON DELETE RESTRICT");
        }

        // Contraintes CHECK nommees (MySQL >= 8.0.16). Ignores sous SQLite (tests en memoire).
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE seller_amounts ADD CONSTRAINT ck_seller_amounts_amount CHECK (amount > 0)");
            DB::statement("ALTER TABLE seller_amounts ADD CONSTRAINT ck_seller_amounts_status CHECK (status IN ('held', 'available', 'paid_out', 'deducted'))");
            DB::statement("ALTER TABLE seller_amounts ADD CONSTRAINT ck_seller_amounts_paid_out CHECK ((status = 'paid_out') = (payout_id IS NOT NULL))");
        }

    }

    public function down(): void
    {
        Schema::dropIfExists('seller_amounts');
    }
};
