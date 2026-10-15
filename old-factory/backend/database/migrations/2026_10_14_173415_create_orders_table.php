<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('orders', function (Blueprint $table) {
            $table->id();
            $table->string('reference', 20)->nullable(false)->comment('Numéro lisible (confirmation RG-026, transmission livreur) — ajout technique');
            $table->bigInteger('customer_id')->unsigned()->nullable(false)->comment('Client passe Commande');
            $table->bigInteger('served_city_id')->unsigned()->nullable(false)->comment('livrée dans (RG-001)');
            $table->string('status', 32)->nullable(false)->default('awaiting_acceptance');
            $table->string('delivery_address', 500)->nullable(false)->comment('adresseLivraison (quartier, adresse, repères : HYPOTHÈSE F007)');
            $table->string('phone', 20)->nullable(false)->comment('téléphone de livraison (RG-014)');
            $table->string('delivery_note', 500)->nullable();
            $table->decimal('delivery_fee', 10, 2)->nullable(false)->comment('fraisLivraison figés à la validation ; valeur = paramètre (Q27 MANQUANT)');
            $table->string('payment_method', 32)->nullable(false)->default('cash_on_delivery');
            $table->decimal('collected_amount', 10, 2)->nullable()->comment('montantEncaissé');
            $table->timestamp('received_at')->nullable()->comment('dateRéception : départ du délai de retour (RG-019, RG-024)');
            $table->string('failure_reason', 500)->nullable()->comment('motifÉchec (RG-013)');
            $table->timestamp('created_at')->nullable()->comment('= date de validation de la commande');
            $table->timestamp('updated_at')->nullable();
            $table->unique('reference');
            $table->index(['customer_id', 'created_at']);
            $table->index(['status', 'created_at']);
            $table->index('served_city_id');
        });

        // Contraintes nommees et FULLTEXT (MySQL >= 8.0.16). Ignores sous SQLite.
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE orders ADD CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE RESTRICT");
            DB::statement("ALTER TABLE orders ADD CONSTRAINT fk_orders_city FOREIGN KEY (served_city_id) REFERENCES served_cities (id) ON DELETE RESTRICT");
        }

        // Contraintes CHECK nommees (MySQL >= 8.0.16). Ignores sous SQLite (tests en memoire).
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE orders ADD CONSTRAINT ck_orders_status CHECK (status IN ('awaiting_acceptance', 'confirmed', 'in_collection', 'out_for_delivery', 'delivered_paid', 'delivery_failed', 'cancelled'))");
            DB::statement("ALTER TABLE orders ADD CONSTRAINT ck_orders_payment_method CHECK (payment_method IN ('cash_on_delivery'))");
            DB::statement("ALTER TABLE orders ADD CONSTRAINT ck_orders_delivery_fee CHECK (delivery_fee >= 0)");
            DB::statement("ALTER TABLE orders ADD CONSTRAINT ck_orders_collected_amount CHECK (collected_amount IS NULL OR collected_amount >= 0)");
            DB::statement("ALTER TABLE orders ADD CONSTRAINT ck_orders_delivered CHECK (status <> 'delivered_paid' OR (collected_amount IS NOT NULL AND received_at IS NOT NULL))");
            DB::statement("ALTER TABLE orders ADD CONSTRAINT ck_orders_failed CHECK (status <> 'delivery_failed' OR failure_reason IS NOT NULL)");
        }

    }

    public function down(): void
    {
        Schema::dropIfExists('orders');
    }
};
