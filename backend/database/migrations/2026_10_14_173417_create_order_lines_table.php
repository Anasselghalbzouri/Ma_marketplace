<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('order_lines', function (Blueprint $table) {
            $table->id();
            $table->bigInteger('sub_order_id')->unsigned()->nullable(false);
            $table->bigInteger('product_id')->unsigned()->nullable(false);
            $table->string('product_name', 200)->nullable(false)->comment('Libellé figé (confirmation RG-026) — ajout technique');
            $table->integer('quantity')->nullable(false);
            $table->decimal('unit_price', 10, 2)->nullable(false)->comment('prixUnitaire figé (RG-007)');
            $table->boolean('is_return_excluded')->nullable(false)->comment('Exclusion du retour figée à la validation (RG-019) — HYPOTHÈSE H-T02-1');
            $table->timestamps();
            $table->unique(['sub_order_id', 'product_id']);
            $table->unique(['id', 'product_id']);
            $table->index('product_id');
        });

        // Contraintes nommees et FULLTEXT (MySQL >= 8.0.16). Ignores sous SQLite.
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE order_lines ADD CONSTRAINT fk_order_lines_sub_order FOREIGN KEY (sub_order_id) REFERENCES sub_orders (id) ON DELETE RESTRICT");
            DB::statement("ALTER TABLE order_lines ADD CONSTRAINT fk_order_lines_product FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE RESTRICT");
        }

        // Contraintes CHECK nommees (MySQL >= 8.0.16). Ignores sous SQLite (tests en memoire).
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE order_lines ADD CONSTRAINT ck_order_lines_quantity_positive CHECK (quantity > 0)");
            DB::statement("ALTER TABLE order_lines ADD CONSTRAINT ck_order_lines_unit_price_positive CHECK (unit_price > 0)");
        }

    }

    public function down(): void
    {
        Schema::dropIfExists('order_lines');
    }
};
