<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('return_inspections', function (Blueprint $table) {
            $table->id();
            $table->bigInteger('product_return_id')->unsigned()->nullable(false);
            $table->string('result', 32)->nullable(false)->comment('RésultatVérification');
            $table->string('dispute_reason', 500)->nullable()->comment('motifContestation');
            $table->boolean('restock')->nullable(false)->comment('remiseEnVente (D43)');
            $table->timestamp('inspected_at')->nullable(false)->comment('date');
            $table->timestamps();
            $table->unique('product_return_id');
        });

        // Contraintes nommees et FULLTEXT (MySQL >= 8.0.16). Ignores sous SQLite.
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE return_inspections ADD CONSTRAINT fk_return_inspections_return FOREIGN KEY (product_return_id) REFERENCES product_returns (id) ON DELETE RESTRICT");
        }

        // Contraintes CHECK nommees (MySQL >= 8.0.16). Ignores sous SQLite (tests en memoire).
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE return_inspections ADD CONSTRAINT ck_return_inspections_result CHECK (result IN ('compliant', 'disputed'))");
            DB::statement("ALTER TABLE return_inspections ADD CONSTRAINT ck_return_inspections_dispute CHECK (result <> 'disputed' OR dispute_reason IS NOT NULL)");
        }

    }

    public function down(): void
    {
        Schema::dropIfExists('return_inspections');
    }
};
