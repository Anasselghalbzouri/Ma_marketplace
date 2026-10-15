<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('sub_orders', function (Blueprint $table) {
            $table->id();
            $table->bigInteger('order_id')->unsigned()->nullable(false);
            $table->bigInteger('seller_id')->unsigned()->nullable(false);
            $table->string('status', 32)->nullable(false)->default('new');
            $table->string('refusal_reason', 500)->nullable()->comment('motifRefus');
            $table->timestamp('response_deadline_at')->nullable(false)->comment('created_at + délai de réponse (paramètre, Q19) figé à la création — ajout technique');
            $table->timestamps();
            $table->unique(['order_id', 'seller_id']);
            $table->index(['seller_id', 'status', 'created_at']);
            $table->index(['status', 'response_deadline_at']);
        });

        // Contraintes nommees et FULLTEXT (MySQL >= 8.0.16). Ignores sous SQLite.
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE sub_orders ADD CONSTRAINT fk_sub_orders_order FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE RESTRICT");
            DB::statement("ALTER TABLE sub_orders ADD CONSTRAINT fk_sub_orders_seller FOREIGN KEY (seller_id) REFERENCES sellers (id) ON DELETE RESTRICT");
        }

        // Contraintes CHECK nommees (MySQL >= 8.0.16). Ignores sous SQLite (tests en memoire).
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE sub_orders ADD CONSTRAINT ck_sub_orders_status CHECK (status IN ('new', 'accepted', 'ready_for_pickup', 'collected', 'refused', 'cancelled'))");
            DB::statement("ALTER TABLE sub_orders ADD CONSTRAINT ck_sub_orders_refused CHECK (status <> 'refused' OR refusal_reason IS NOT NULL)");
        }

    }

    public function down(): void
    {
        Schema::dropIfExists('sub_orders');
    }
};
