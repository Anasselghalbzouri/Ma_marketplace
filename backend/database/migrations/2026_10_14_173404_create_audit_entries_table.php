<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('audit_entries', function (Blueprint $table) {
            $table->id();
            $table->timestamp('occurred_at', 3)->nullable(false);
            $table->bigInteger('actor_user_id')->unsigned()->nullable()->comment('NULL seulement pour un traitement planifié');
            $table->string('actor_system', 64)->nullable()->comment('Code du traitement planifié si acteur système');
            $table->string('action_type', 48)->nullable(false);
            $table->string('target_type', 48)->nullable(false)->comment('Référence logique (ex. sub_order, seller_amount)');
            $table->bigInteger('target_id')->unsigned()->nullable(false);
            $table->string('from_status', 32)->nullable();
            $table->string('to_status', 32)->nullable();
            $table->decimal('amount', 10, 2)->nullable();
            $table->string('reason', 500)->nullable();
            $table->bigInteger('corrects_entry_id')->unsigned()->nullable();
            $table->index(['target_type', 'target_id', 'occurred_at']);
            $table->index(['actor_user_id', 'occurred_at']);
            $table->index(['action_type', 'occurred_at']);
        });

        // Contraintes nommees et FULLTEXT (MySQL >= 8.0.16). Ignores sous SQLite.
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE audit_entries ADD CONSTRAINT fk_audit_actor FOREIGN KEY (actor_user_id) REFERENCES users (id) ON DELETE RESTRICT");
            DB::statement("ALTER TABLE audit_entries ADD CONSTRAINT fk_audit_corrects FOREIGN KEY (corrects_entry_id) REFERENCES audit_entries (id) ON DELETE RESTRICT");
        }

        // Contraintes CHECK nommees (MySQL >= 8.0.16). Ignores sous SQLite (tests en memoire).
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE audit_entries ADD CONSTRAINT ck_audit_actor CHECK (actor_user_id IS NOT NULL OR actor_system IS NOT NULL)");
            DB::statement("ALTER TABLE audit_entries ADD CONSTRAINT ck_audit_action CHECK (action_type IN ( 'order_status_changed', 'sub_order_status_changed', 'delivery_status_recorded', 'cash_collected', 'fund_remittance_recorded', 'cash_discrepancy_recorded', 'seller_amount_held', 'seller_amount_released', 'seller_amount_deducted', 'return_status_changed', 'return_pickup_recorded', 'return_fee_charged', 'dispute_decided', 'refund_recorded', 'deduction_recorded', 'payout_recorded', 'correction', 'scheduled_task_run'))");
            DB::statement("ALTER TABLE audit_entries ADD CONSTRAINT ck_audit_money CHECK (action_type NOT IN ('cash_collected', 'fund_remittance_recorded', 'cash_discrepancy_recorded', 'seller_amount_deducted', 'return_fee_charged', 'refund_recorded', 'deduction_recorded', 'payout_recorded', 'correction') OR (amount IS NOT NULL AND reason IS NOT NULL))");
            DB::statement("ALTER TABLE audit_entries ADD CONSTRAINT ck_audit_correction CHECK (action_type <> 'correction' OR corrects_entry_id IS NOT NULL)");
        }

    }

    public function down(): void
    {
        Schema::dropIfExists('audit_entries');
    }
};
