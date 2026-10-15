<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('sellers', function (Blueprint $table) {
            $table->id();
            $table->bigInteger('user_id')->unsigned()->nullable(false);
            $table->string('legal_name', 200)->nullable(false)->comment('identitéRaisonSociale');
            $table->bigInteger('seller_commune_id')->unsigned()->nullable(false)->comment('situé dans (RG-023)');
            $table->string('payout_method', 32)->nullable(false)->comment('ModeReversement');
            $table->text('bank_details')->nullable();
            $table->string('chiffré', 255)->nullable();
            $table->string('status', 32)->nullable(false)->default('active');
            $table->timestamp('suspended_at')->nullable();
            $table->timestamps();
            $table->unique('user_id');
            $table->index('seller_commune_id');
            $table->index('status');
        });

        // Contraintes nommees et FULLTEXT (MySQL >= 8.0.16). Ignores sous SQLite.
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE sellers ADD CONSTRAINT fk_sellers_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE RESTRICT");
            DB::statement("ALTER TABLE sellers ADD CONSTRAINT fk_sellers_commune FOREIGN KEY (seller_commune_id) REFERENCES seller_communes (id) ON DELETE RESTRICT");
        }

        // Contraintes CHECK nommees (MySQL >= 8.0.16). Ignores sous SQLite (tests en memoire).
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE sellers ADD CONSTRAINT ck_sellers_payout_method CHECK (payout_method IN ('bank_transfer', 'cash'))");
            DB::statement("ALTER TABLE sellers ADD CONSTRAINT ck_sellers_bank_details CHECK (payout_method <> 'bank_transfer' OR bank_details IS NOT NULL)");
            DB::statement("ALTER TABLE sellers ADD CONSTRAINT ck_sellers_status CHECK (status IN ('active', 'suspended'))");
            DB::statement("ALTER TABLE sellers ADD CONSTRAINT ck_sellers_suspended_at CHECK (status <> 'suspended' OR suspended_at IS NOT NULL)");
        }

    }

    public function down(): void
    {
        Schema::dropIfExists('sellers');
    }
};
