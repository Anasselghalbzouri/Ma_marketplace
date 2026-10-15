<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('return_fees', function (Blueprint $table) {
            $table->id();
            $table->bigInteger('product_return_id')->unsigned()->nullable(false);
            $table->decimal('amount', 10, 2)->nullable(false);
            $table->string('charged_to', 32)->nullable(false)->comment('imputéÀ : ImputationFrais');
            $table->timestamps();
            $table->unique('product_return_id');
        });

        // Contraintes nommees et FULLTEXT (MySQL >= 8.0.16). Ignores sous SQLite.
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE return_fees ADD CONSTRAINT fk_return_fees_return FOREIGN KEY (product_return_id) REFERENCES product_returns (id) ON DELETE RESTRICT");
        }

        // Contraintes CHECK nommees (MySQL >= 8.0.16). Ignores sous SQLite (tests en memoire).
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE return_fees ADD CONSTRAINT ck_return_fees_amount CHECK (amount >= 0)");
            DB::statement("ALTER TABLE return_fees ADD CONSTRAINT ck_return_fees_charged_to CHECK (charged_to IN ('customer', 'seller'))");
        }

    }

    public function down(): void
    {
        Schema::dropIfExists('return_fees');
    }
};
