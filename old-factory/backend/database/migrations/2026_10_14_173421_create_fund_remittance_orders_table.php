<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('fund_remittance_orders', function (Blueprint $table) {
            $table->bigInteger('fund_remittance_id')->unsigned()->nullable(false);
            $table->bigInteger('order_id')->unsigned()->nullable(false);
            $table->index('order_id');
        });

        // Contraintes nommees et FULLTEXT (MySQL >= 8.0.16). Ignores sous SQLite.
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE fund_remittance_orders ADD CONSTRAINT fk_fro_remittance FOREIGN KEY (fund_remittance_id) REFERENCES fund_remittances (id) ON DELETE RESTRICT");
            DB::statement("ALTER TABLE fund_remittance_orders ADD CONSTRAINT fk_fro_order FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE RESTRICT");
        }

    }

    public function down(): void
    {
        Schema::dropIfExists('fund_remittance_orders');
    }
};
