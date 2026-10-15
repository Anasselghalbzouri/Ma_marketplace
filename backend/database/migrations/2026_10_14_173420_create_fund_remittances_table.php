<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('fund_remittances', function (Blueprint $table) {
            $table->id();
            $table->bigInteger('delivery_partner_id')->unsigned()->nullable(false)->comment('SociétéDeLivraison remet');
            $table->decimal('amount', 10, 2)->nullable(false);
            $table->string('remitted_on', 255)->nullable(false)->comment('date');
            $table->bigInteger('recorded_by_user_id')->unsigned()->nullable(false)->comment('Administrateur (saisie, RG-029)');
            $table->timestamps();
            $table->index(['delivery_partner_id', 'remitted_on']);
        });

        // Contraintes nommees et FULLTEXT (MySQL >= 8.0.16). Ignores sous SQLite.
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE fund_remittances ADD CONSTRAINT fk_fund_remittances_partner FOREIGN KEY (delivery_partner_id) REFERENCES delivery_partners (id) ON DELETE RESTRICT");
            DB::statement("ALTER TABLE fund_remittances ADD CONSTRAINT fk_fund_remittances_recorder FOREIGN KEY (recorded_by_user_id) REFERENCES users (id) ON DELETE RESTRICT");
        }

        // Contraintes CHECK nommees (MySQL >= 8.0.16). Ignores sous SQLite (tests en memoire).
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE fund_remittances ADD CONSTRAINT ck_fund_remittances_amount CHECK (amount > 0)");
        }

    }

    public function down(): void
    {
        Schema::dropIfExists('fund_remittances');
    }
};
