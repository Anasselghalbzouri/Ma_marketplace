<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('products', function (Blueprint $table) {
            $table->id();
            $table->bigInteger('shop_id')->unsigned()->nullable(false)->comment('Boutique publie Produit');
            $table->bigInteger('category_id')->unsigned()->nullable(false);
            $table->string('name', 200)->nullable(false);
            $table->text('description')->nullable(false);
            $table->decimal('price', 10, 2)->nullable(false);
            $table->string('prix', 255)->nullable();
            $table->integer('stock')->nullable(false)->default(0);
            $table->string('origin', 150)->nullable()->comment('origine ville/région (HYPOTHÈSE F003)');
            $table->boolean('is_perishable')->nullable(false)->default(false);
            $table->boolean('is_customized')->nullable(false)->default(false);
            $table->boolean('is_published')->nullable(false)->default(false);
            $table->boolean('is_hidden')->nullable(false)->default(false)->comment('masqué par l\'administrateur (RG-015)');
            $table->timestamp('hidden_at')->nullable();
            $table->timestamps();
            $table->timestamp('deleted_at')->nullable()->comment('Suppression logique : un produit commandé reste référencé');
            $table->index('shop_id');
            $table->index(['category_id', 'is_published', 'is_hidden', 'stock']);
            $table->index(['is_published', 'is_hidden', 'stock', 'created_at']);
        });

        // Contraintes nommees et FULLTEXT (MySQL >= 8.0.16). Ignores sous SQLite.
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE products ADD CONSTRAINT fk_products_shop FOREIGN KEY (shop_id) REFERENCES shops (id) ON DELETE RESTRICT");
            DB::statement("ALTER TABLE products ADD CONSTRAINT fk_products_category FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE RESTRICT");
            DB::statement("ALTER TABLE products ADD FULLTEXT INDEX ft_products_search (name, description)");
        }

        // Contraintes CHECK nommees (MySQL >= 8.0.16). Ignores sous SQLite (tests en memoire).
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE products ADD CONSTRAINT ck_products_price_positive CHECK (price > 0)");
            DB::statement("ALTER TABLE products ADD CONSTRAINT ck_products_stock_non_negative CHECK (stock >= 0)");
            DB::statement("ALTER TABLE products ADD CONSTRAINT ck_products_hidden_at CHECK (is_hidden = FALSE OR hidden_at IS NOT NULL)");
        }

    }

    public function down(): void
    {
        Schema::dropIfExists('products');
    }
};
